# -*- coding: utf-8 -*-
"""
Created on Fri Apr 19 13:48:51 2019

@author: umorf

The module contains the functions which are used to split the stiffness and the
force matrix into unrestricted and restricted components.
"""

import numpy as np
import scipy.sparse as sps


def apply_boundary_conditions(boundary_conditions, stiffness_matrix, force_matrix):
    """Splits the stiffness and the force matrices according to the boundary conditions.
    
    Arguments:
        boundary_conditions -- the boundary conditions of the system
        stiffness_matrix    -- the stiffness matrix of the system, not including
                               restricted degrees
        force_matrix        -- a matrix combining the global force vectors of 
                               the different loadgroups
        
    Return values:
        stiffness_and_force_matrices -- the stiffness and force matrices of the
                                        restricted and the unrestricted nodal
                                        directions
    """
    restricted_degrees = boundary_conditions['Restricted Degrees']
    springs = boundary_conditions['Springs']
    rotated_degrees = boundary_conditions['Rotated Degrees']

    size = stiffness_matrix.shape[0]

    # Determine the nodal directions which are restricted.    
    indices = get_indices_todelete(restricted_degrees)

    # Get the matrices that can delete certain rows or columns
    (delete_rows, delete_columns, keep_rows, keep_columns) = modifier_matrices(size, indices)

    r, rt = rotation_matrices(size, rotated_degrees)

    # Delete the determined nodes with the help of the modifier matrices.
    force_matrix_modified = delete_rows @ r @ force_matrix
    force_matrix_supports = keep_rows @ r @ force_matrix

    stiffness_mat = r @ stiffness_matrix @ rt

    # Include springs
    for spring in springs:
        i = spring[0]
        stiffness_mat[3*i, 3*i] += spring[1]
        stiffness_mat[3*i+1, 3*i+1] += spring[2]
        stiffness_mat[3*i+2, 3*i+2] += spring[3]

    stiffness_matrix_modified = delete_rows @ stiffness_mat @ delete_columns
    stiffness_matrix_supports = keep_rows @ stiffness_mat @ delete_columns

    stiffness_and_force_matrices = [stiffness_matrix_modified,
                                    stiffness_matrix_supports,
                                    force_matrix_modified,
                                    force_matrix_supports,
                                    r, rt]
    return stiffness_and_force_matrices


def rotation_matrices(original_size, rotated_degrees):
    components = np.ones(original_size)
    count1 = np.arange(original_size)
    count2 = np.arange(original_size)
    for rotated_degree in rotated_degrees:
        index = rotated_degree[0]*3
        angle = rotated_degree[1]
        if angle != 0:
            c, s = np.cos(angle), np.sin(angle)
            components = np.concatenate([components, np.array([c-1, -s, s, c-1])])
            count1 = np.concatenate([count1, np.array([index, index, index+1, index+1])])
            count2 = np.concatenate([count2, np.array([index, index+1, index, index+1])])

    r1 = sps.csr_matrix((components, (count1, count2)), (original_size, original_size))
    rt = sps.csr_matrix((components, (count2, count1)), (original_size, original_size))
    return r1, rt


def modifier_matrices(original_size, indices):
    """Creates matrices that can keep or delete certain indices from a square matrix.
    
    It creates the four matrices to delete or extract the specified indices
    (rows or columns).
    
    Keyword argument:
        original_size -- the original amount of indices
        indices       -- a numpy vector of the indices which are to be kept or 
                         deleted
        
    Return values:
        delete_rows    -- a matrix which deletes the specified indices rows
                          from a matrix with original_size rows
        delete_columns -- a matrix which deletes the specified indices columns
                          from a matrix with original_size columns
        keep_rows      -- a matrix which extracts the specified indices rows
                          from a matrix with original_size rows
        keep_columns   -- a matrix which extracts the specified indices columns
                          from a matrix with original_size columns
    """
    amount_todelete = indices.shape[0]
    new_size = original_size - amount_todelete

    # List of the elements which are to be kept or killed
    elements_original = np.arange(original_size)
    elements_keep = np.delete(elements_original, indices, None)
    elements_kill = indices

    # List of ones for each element to kill or keep
    ones_kill = np.ones(new_size)
    ones_keep = np.ones(amount_todelete)

    # Normal Count for the elements to kill or keep
    count_kill = np.arange(new_size)
    count_keep = np.arange(amount_todelete)

    # Create the sparse matrices to delete or keep the specified rows or cols.
    delete_rows = sps.csr_matrix((ones_kill, (count_kill, elements_keep)),
                                 (new_size, original_size))

    delete_columns = sps.csr_matrix((ones_kill, (elements_keep, count_kill)),
                                    (original_size, new_size))
    if any(ones_keep):
        keep_rows = sps.csr_matrix((ones_keep, (count_keep, elements_kill)),
                                   (amount_todelete, original_size))

        keep_columns = sps.csr_matrix((ones_keep, (elements_kill, count_keep)),
                                      (original_size, amount_todelete))
    else:
        keep_rows = sps.csr_matrix(([], ([], [])), (amount_todelete, original_size))
        keep_columns = sps.csr_matrix(([], ([], [])), (original_size, amount_todelete))

    return delete_rows, delete_columns, keep_rows, keep_columns


def get_indices_todelete(restricted_degrees):
    """Gives a numpy vector of the nodal degrees of freedom which are to be deleted.
    
    Arguments:
        restricted_degrees -- the restricted degrees of the system 
    
    Return values:
        indices_rdofs -- a numpy vector containing all the nodal degrees of
                            freedom which are to be deleted
    """
    indices_rdofs = np.empty((0, 0), dtype=int)

    # Append the list for each restricted nodal degree of freedom
    for restricted_degree in restricted_degrees:
        if restricted_degree[1] == 1:
            indices_rdofs = np.append(indices_rdofs, restricted_degree[0] * 3 + 0)

        if restricted_degree[2] == 1:
            indices_rdofs = np.append(indices_rdofs, restricted_degree[0] * 3 + 1)

        if restricted_degree[3] == 1:
            indices_rdofs = np.append(indices_rdofs, restricted_degree[0] * 3 + 2)

    return indices_rdofs
